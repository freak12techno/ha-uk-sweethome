import logging

import async_timeout
from homeassistant.helpers.discovery import async_load_platform
from mosenergosbyt import Session, Account
from .const import *
import voluptuous as vol
from homeassistant.core import callback, HomeAssistant
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
import pkg_resources
from datetime import datetime
from .client import UkSweethomeClient

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, base_config: dict):
    config = base_config[DOMAIN]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    client = UkSweethomeClient(hass, username, password)
    hass.data[DOMAIN] = client

    info = client.accounting()
    _LOGGER.debug("got accounting: {info}")

    # meter_list = await client.fetch_data()

    # if meter_list:
    #     _LOGGER.debug("счетчики получены")
    #     hass.async_create_task(
    #         async_load_platform(
    #             hass,
    #             SENSOR_DOMAIN,
    #             DOMAIN,
    #             discovered={meter.nn_ls: meter.nn_ls for meter in meter_list.values()},
    #             hass_config=config,
    #         )
    #     )

    # async def publish_electricity_usage(call):
    #     await hass.async_add_executor_job(
    #         client.upload_measure,
    #         call.data[CONF_PAYCODE],
    #         call.data[VOLUME_DAY],
    #         call.data.get(VOLUME_NIGHT, None),
    #         call.data.get(VOLUME_MIDDLE, None)
    #     )

    # hass.services.async_register(DOMAIN, 'publish_electricity_usage', publish_electricity_usage)

    return True


class PortalWrap:
    def __init__(self, **kwargs):
        self.hass = kwargs['hass']
        self.account = kwargs['account']
        self.last_update = None

    def get_meters_list(self):
        try:
            #кеш на минуту, чтобы предотвратить лишние запросы на портал
            if self.last_update and (datetime.now() - self.last_update).total_seconds() < 60:
                return self.account.meter_list

            self.account.get_info(with_measure=True, indications=True, balance=True)
            self.last_update = datetime.now()

            return self.account.meter_list
        except BaseException as e:
            _LOGGER.error(f'ошибка получения данных {e}')

    async def fetch_data(self):
        async with async_timeout.timeout(20) as at:
            data = await self.hass.async_add_executor_job(
                self.get_meters_list
            )
        if at.expired:
            _LOGGER.error('таймаут получения данных с портала')
        return data
